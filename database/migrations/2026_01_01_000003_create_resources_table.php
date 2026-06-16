<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class () extends Migration {
    public function up(): void
    {
        Schema::create('resources', function (Blueprint $table) {
            $table->id();
            $table->foreignId('event_id')->constrained()->cascadeOnDelete();
            $table->string('name');
            $table->string('resource_type', 20);
            $table->string('status', 20)->default('available');
            $table->string('availability', 20)->default('available');
            $table->string('highest_clinical_level', 20)->nullable();
            $table->boolean('is_deployable')->default(false);
            $table->timestamps();

            $table->unique(['event_id', 'name']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('resources');
    }
};
